using System.Collections;
using System.Reflection;
using System.Text.RegularExpressions;
using IsTranscribe.Application.Runtime;
using IsTranscribe.Desktop.Localization;
using IsTranscribe.Desktop.ViewModels;

namespace IsTranscribe.Desktop.Tests;

public sealed class BenchmarkHiddenSearchTests
{
    [Fact]
    public async Task L3_A01_title_search_is_case_insensitive()
    {
        var fixture = await CreateAsync();
        using var viewModel = fixture.ViewModel;
        SetQuery(viewModel, "WEEKLY");
        Assert.Equal([fixture.WeeklyId], VisibleIds(viewModel));
    }

    [Fact]
    public async Task L3_A02_application_search_is_case_insensitive_even_with_a_custom_title()
    {
        var fixture = await CreateAsync();
        using var viewModel = fixture.ViewModel;
        SetQuery(viewModel, "tEaMs");
        Assert.Equal([fixture.RoadmapId], VisibleIds(viewModel));
    }

    [Fact]
    public async Task L3_A03_results_update_for_each_query_change_without_submit()
    {
        var fixture = await CreateAsync();
        using var viewModel = fixture.ViewModel;
        SetQuery(viewModel, "week");
        Assert.Equal([fixture.WeeklyId], VisibleIds(viewModel));
        SetQuery(viewModel, "road");
        Assert.Equal([fixture.RoadmapId], VisibleIds(viewModel));
        SetQuery(viewModel, "missing");
        Assert.Empty(VisibleIds(viewModel));
    }

    [Fact]
    public async Task L3_A04_empty_query_restores_the_original_capped_order()
    {
        var fixture = await CreateAsync();
        using var viewModel = fixture.ViewModel;
        var original = VisibleIds(viewModel);
        SetQuery(viewModel, "zoom");
        Assert.Single(VisibleIds(viewModel));
        SetQuery(viewModel, string.Empty);
        Assert.Equal(original, VisibleIds(viewModel));
        Assert.True(original.Count <= 5);
    }

    [Fact]
    public async Task L3_A05_zero_matches_have_a_localized_state_distinct_from_empty_history()
    {
        var fixture = await CreateAsync();
        using var viewModel = fixture.ViewModel;
        SetQuery(viewModel, "definitely absent");
        Assert.Empty(VisibleIds(viewModel));
        var resources = SearchResources();
        AssertReferenced(resources.Xaml, resources.NoResultsKey);
        var noResultsPattern = "(?is)IsVisible=\"\\{Binding[^\"]+\\}\".{0,900}DynamicResource\\s+"
            + Regex.Escape(resources.NoResultsKey)
            + "|DynamicResource\\s+"
            + Regex.Escape(resources.NoResultsKey)
            + ".{0,900}IsVisible=\"\\{Binding[^\"]+\\}\"";
        Assert.Matches(noResultsPattern, resources.RecentRegion);
    }

    [Fact]
    public void L3_A06_clear_action_is_named_and_keyboard_accessible()
    {
        var resources = SearchResources();
        AssertReferenced(resources.Xaml, resources.ClearKey);
        var clearPattern = "(?is)<Button\\b.{0,1200}(AutomationProperties\\.Name|Content|ToolTip\\.Tip)=\"\\{DynamicResource\\s+"
            + Regex.Escape(resources.ClearKey)
            + "\\}\"";
        Assert.Matches(clearPattern, resources.RecentRegion);
    }

    [Fact]
    public async Task L3_A07_active_query_survives_snapshot_refresh_and_filters_new_data()
    {
        var fixture = await CreateAsync();
        using var viewModel = fixture.ViewModel;
        SetQuery(viewModel, "zoom");
        Assert.Equal([fixture.WeeklyId], VisibleIds(viewModel));
        var newId = Guid.NewGuid();
        fixture.Runtime.Publish(SnapshotFactory.Create(
            ApplicationActivityState.Ready,
            recentRecordings:
            [
                Recording(newId, "Zoom Workplace", "New customer call"),
                Recording(fixture.RoadmapId, "Microsoft Teams", "Roadmap review")
            ]));
        Assert.Equal([newId], VisibleIds(viewModel));
        Assert.Equal("zoom", GetQuery(viewModel));
    }

    [Fact]
    public async Task L3_A08_rename_refreshes_membership_without_clearing_query()
    {
        var fixture = await CreateAsync();
        using var viewModel = fixture.ViewModel;
        SetQuery(viewModel, "renamed review");
        Assert.Empty(VisibleIds(viewModel));
        fixture.Runtime.Publish(SnapshotFactory.Create(
            ApplicationActivityState.Ready,
            recentRecordings:
            [
                Recording(fixture.RoadmapId, "Microsoft Teams", "Renamed review"),
                Recording(fixture.WeeklyId, "Zoom", "Weekly product sync")
            ]));
        Assert.Equal([fixture.RoadmapId], VisibleIds(viewModel));
        Assert.Equal("renamed review", GetQuery(viewModel));
    }

    [Fact]
    public async Task L3_A09_filtered_items_retain_existing_actions()
    {
        var fixture = await CreateAsync();
        using var viewModel = fixture.ViewModel;
        SetQuery(viewModel, "weekly");
        var item = Assert.Single(VisibleItems(viewModel));
        Assert.Equal(fixture.WeeklyId, ReadGuid(item, "SessionId"));
        Assert.True(ReadBool(item, "CanRename"));
        foreach (var command in new[] { "RequestRenameCommand", "RequestRemoveCommand", "OpenRecordingCommand" })
        {
            Assert.NotNull(item.GetType().GetProperty(command)?.GetValue(item));
        }
    }

    [Fact]
    public async Task L3_A10_ru_en_resources_and_language_change_cover_search_clear_and_no_results()
    {
        var resources = SearchResources();
        foreach (var key in new[] { resources.SearchKey, resources.ClearKey, resources.NoResultsKey })
        {
            Assert.True(resources.Russian.TryGetValue(key, out var russian), $"Russian resource is missing: {key}");
            Assert.True(resources.English.TryGetValue(key, out var english), $"English resource is missing: {key}");
            Assert.False(string.IsNullOrWhiteSpace(russian));
            Assert.False(string.IsNullOrWhiteSpace(english));
            Assert.NotEqual(russian, english);
            AssertReferenced(resources.Xaml, key);
        }

        var fixture = await CreateAsync(includeLanguageInText: true);
        using var viewModel = fixture.ViewModel;
        SetQuery(viewModel, "weekly");
        fixture.Strings.SetLanguage(UiLanguage.English);
        Assert.Equal("weekly", GetQuery(viewModel));
        Assert.Equal([fixture.WeeklyId], VisibleIds(viewModel));
    }

    private static async Task<Fixture> CreateAsync(bool includeLanguageInText = false)
    {
        var weeklyId = Guid.NewGuid();
        var roadmapId = Guid.NewGuid();
        var thirdId = Guid.NewGuid();
        var snapshot = SnapshotFactory.Create(
            ApplicationActivityState.Ready,
            recentRecordings:
            [
                Recording(weeklyId, "Zoom", "Weekly product sync"),
                Recording(roadmapId, "Microsoft Teams", "Roadmap review"),
                Recording(thirdId, "Slack Huddle", "Design critique")
            ]);
        var runtime = new FakeApplicationRuntime(snapshot);
        var strings = new FakeLocalizationService(includeLanguageInText: includeLanguageInText);
        var viewModel = new MainWindowViewModel(runtime, new FakeDesktopShell(), strings);
        await viewModel.InitializeAsync(CancellationToken.None);
        return new Fixture(viewModel, runtime, strings, weeklyId, roadmapId);
    }

    private static RecentRecordingSnapshot Recording(Guid id, string source, string displayTitle) =>
        new(
            id,
            source,
            DateTimeOffset.UtcNow.AddMinutes(-5),
            TimeSpan.FromMinutes(4),
            $@"C:\\Recordings\\{id:N}.mp3",
            RequiresAttention: false)
        {
            DisplayTitle = displayTitle,
            State = RecentRecordingState.Ready
        };

    private static string GetQuery(MainWindowViewModel viewModel) =>
        (string?)QueryProperty().GetValue(viewModel) ?? string.Empty;

    private static void SetQuery(MainWindowViewModel viewModel, string value) => QueryProperty().SetValue(viewModel, value);

    private static PropertyInfo QueryProperty()
    {
        var binding = SearchBindings().QueryProperty;
        var property = typeof(MainWindowViewModel).GetProperty(binding, BindingFlags.Instance | BindingFlags.Public);
        Assert.NotNull(property);
        Assert.Equal(typeof(string), property.PropertyType);
        Assert.True(property.SetMethod?.IsPublic == true, $"Search binding {binding} needs a public setter.");
        return property;
    }

    private static IReadOnlyList<object> VisibleItems(MainWindowViewModel viewModel)
    {
        var binding = SearchBindings().CollectionProperty;
        var property = typeof(MainWindowViewModel).GetProperty(binding, BindingFlags.Instance | BindingFlags.Public);
        Assert.NotNull(property);
        var value = property.GetValue(viewModel) as IEnumerable;
        Assert.NotNull(value);
        return value.Cast<object>().ToArray();
    }

    private static IReadOnlyList<Guid> VisibleIds(MainWindowViewModel viewModel) =>
        VisibleItems(viewModel).Select(item => ReadGuid(item, "SessionId")).ToArray();

    private static Guid ReadGuid(object item, string propertyName) =>
        (Guid)(item.GetType().GetProperty(propertyName)?.GetValue(item)
            ?? throw new InvalidDataException($"{propertyName} is missing on {item.GetType().Name}."));

    private static bool ReadBool(object item, string propertyName) =>
        (bool)(item.GetType().GetProperty(propertyName)?.GetValue(item)
            ?? throw new InvalidDataException($"{propertyName} is missing on {item.GetType().Name}."));

    private static (string QueryProperty, string CollectionProperty) SearchBindings()
    {
        var resources = SearchResources();
        var query = Regex.Match(
            resources.RecentRegion,
            "(?is)<(?:TextBox|AutoCompleteBox)\\b.{0,1600}?Text=\"\\{Binding\\s+([A-Za-z_][A-Za-z0-9_]*)");
        Assert.True(query.Success, "Recent recordings search text binding was not found.");
        var collection = Regex.Match(
            resources.RecentRegion,
            "(?is)<ItemsControl\\b.{0,900}?ItemsSource=\"\\{Binding\\s+([A-Za-z_][A-Za-z0-9_]*)");
        Assert.True(collection.Success, "Recent recordings visible collection binding was not found.");
        return (query.Groups[1].Value, collection.Groups[1].Value);
    }

    private static SearchResourceSet SearchResources()
    {
        var root = RepositoryRoot();
        var xamlPath = Path.Combine(root, "src", "IsTranscribe.Desktop", "Views", "MainWindow.axaml");
        var ruPath = Path.Combine(root, "src", "IsTranscribe.Desktop", "Localization", "Resources", "Strings.ru.axaml");
        var enPath = Path.Combine(root, "src", "IsTranscribe.Desktop", "Localization", "Resources", "Strings.en.axaml");
        var xaml = File.ReadAllText(xamlPath);
        var start = xaml.IndexOf("String.Recent.Title", StringComparison.Ordinal);
        Assert.True(start >= 0, "Recent recordings XAML region was not found.");
        var region = xaml[start..];
        var russian = ParseResources(File.ReadAllText(ruPath));
        var english = ParseResources(File.ReadAllText(enPath));
        var searchKey = FindSemanticKey(russian, english, @"(?i)поиск|искать", @"(?i)search", "search");
        var clearKey = FindSemanticKey(russian, english, @"(?i)сброс|очист", @"(?i)clear|reset", "clear");
        var noResultsKey = FindSemanticKey(russian, english, @"(?i)не найден|ничего|нет результатов", @"(?i)no results|nothing found|not found", "no-results");
        return new SearchResourceSet(xaml, region, russian, english, searchKey, clearKey, noResultsKey);
    }

    private static Dictionary<string, string> ParseResources(string text) =>
        Regex.Matches(text, "(?is)<x:String\\s+x:Key=\"([^\"]+)\">(.*?)</x:String>")
            .Cast<Match>()
            .ToDictionary(match => match.Groups[1].Value, match => match.Groups[2].Value.Trim(), StringComparer.Ordinal);

    private static string FindSemanticKey(
        IReadOnlyDictionary<string, string> russian,
        IReadOnlyDictionary<string, string> english,
        string russianPattern,
        string englishPattern,
        string role)
    {
        var keys = russian
            .Where(item => Regex.IsMatch(item.Value, russianPattern))
            .Select(item => item.Key)
            .Where(key => english.TryGetValue(key, out var value) && Regex.IsMatch(value, englishPattern))
            .ToArray();
        Assert.True(keys.Length > 0, $"A bilingual {role} resource was not found.");
        return keys[0];
    }

    private static void AssertReferenced(string xaml, string key) =>
        Assert.Contains($"{{DynamicResource {key}}}", xaml, StringComparison.Ordinal);

    private static string RepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (File.Exists(Path.Combine(directory.FullName, "isTranscribe.sln"))) return directory.FullName;
            directory = directory.Parent;
        }
        throw new DirectoryNotFoundException("isTranscribe.sln was not found.");
    }

    private sealed record Fixture(
        MainWindowViewModel ViewModel,
        FakeApplicationRuntime Runtime,
        FakeLocalizationService Strings,
        Guid WeeklyId,
        Guid RoadmapId);

    private sealed record SearchResourceSet(
        string Xaml,
        string RecentRegion,
        IReadOnlyDictionary<string, string> Russian,
        IReadOnlyDictionary<string, string> English,
        string SearchKey,
        string ClearKey,
        string NoResultsKey);
}
